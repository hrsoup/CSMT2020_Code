import torch
import torch.nn.functional as F

def word2features(sent, i):
    word = sent[i]
    prev_word = "<s>" if i == 0 else sent[i-1]
    next_word = "</s>" if i == (len(sent)-1) else sent[i+1]
    features = {
        'w-1, w, w+1': prev_word+word+next_word
    }
    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]


def tensorized(batch, maps):
    PAD = maps.get('<pad>')
    UNK = maps.get('<unk>')

    max_len = len(batch[0])
    batch_size = len(batch)

    batch_tensor = torch.ones(batch_size, max_len).long() * PAD
    for i, l in enumerate(batch):
        for j, e in enumerate(l):
            batch_tensor[i][j] = maps.get(e, UNK)
    lengths = [len(l) for l in batch]

    return batch_tensor, lengths


def sort_by_lengths(word_lists, tag_lists):
    pairs = list(zip(word_lists, tag_lists))
    indices = sorted(range(len(pairs)),
                     key=lambda k: len(pairs[k][0]),
                     reverse=True)
    pairs = [pairs[i] for i in indices]
    # pairs.sort(key=lambda pair: len(pair[0]), reverse=True)

    word_lists, tag_lists = list(zip(*pairs))

    return word_lists, tag_lists, indices


def cal_loss(logits, targets, tag2id):
    """计算损失
    参数:
        logits: [B, L, out_size]
        targets: [B, L]
        lengths: [B]
    """
    PAD = tag2id.get('<pad>')
    assert PAD is not None

    mask = (targets != PAD)  # [B, L]
    targets = targets[mask]
    out_size = logits.size(2)
    logits = logits.masked_select(
        mask.unsqueeze(2).expand(-1, -1, out_size)
    ).contiguous().view(-1, out_size)

    assert logits.size(0) == targets.size(0)
    loss = F.cross_entropy(logits, targets)

    return loss

# FOR BiLSTM-CRF


def cal_lstm_crf_loss(crf_scores, targets, tag2id):

    pad_id = tag2id.get('<pad>')
    start_id = tag2id.get('<start>')
    end_id = tag2id.get('<end>')

    device = crf_scores.device

    # targets:[B, L] crf_scores:[B, L, T, T]
    batch_size, max_len = targets.size()
    target_size = len(tag2id)

    # mask = 1 - ((targets == pad_id) + (targets == end_id))  # [B, L]
    mask = (targets != pad_id)
    lengths = mask.sum(dim=1)
    targets = indexed(targets, target_size, start_id)

    targets = targets.masked_select(mask)  # [real_L]

    flatten_scores = crf_scores.masked_select(
        mask.view(batch_size, max_len, 1, 1).expand_as(crf_scores)
    ).view(-1, target_size*target_size).contiguous()

    golden_scores = flatten_scores.gather(
        dim=1, index=targets.unsqueeze(1)).sum()

    scores_upto_t = torch.zeros(batch_size, target_size).to(device)
    for t in range(max_len):
        batch_size_t = (lengths > t).sum().item()
        if t == 0:
            scores_upto_t[:batch_size_t] = crf_scores[:batch_size_t,
                                                      t, start_id, :]
        else:
            scores_upto_t[:batch_size_t] = torch.logsumexp(
                crf_scores[:batch_size_t, t, :, :] +
                scores_upto_t[:batch_size_t].unsqueeze(2),
                dim=1
            )
    all_path_scores = scores_upto_t[:, end_id].sum()

    loss = (all_path_scores - golden_scores) / batch_size
    return loss


def indexed(targets, tagset_size, start_id):
    batch_size, max_len = targets.size()
    for col in range(max_len-1, 0, -1):
        targets[:, col] += (targets[:, col-1] * tagset_size)
    targets[:, 0] += (start_id * tagset_size)
    return targets
