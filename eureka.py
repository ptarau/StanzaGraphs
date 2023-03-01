import numpy as np
import matplotlib.pyplot as plt


def softmax(x):
    """Compute softmax values for a given array of numbers."""
    exp_x = np.exp(x)
    return exp_x / np.sum(exp_x, axis=0)


# Example usage
# x = np.array([10, 1, 1, 1, 1, 10])
# softmax_x = softmax(x)
# print(softmax_x)


def forward_leaning(sent_count):
    """
    rebalances ranks to prioritize
    abstract and inro of a scientific paper
    for better extractive summarization
    """

    intro_guess = min(64, max(32, (10 * sent_count) // 100))

    ns = list(reversed(range(2, 2 + intro_guess)))

    ns.extend([1] * (sent_count - intro_guess))

    rs = [n ** 0.5 for n in ns]
    # print(ns)

    rs = softmax(np.array(rs))
    rs = [sent_count * round(x, 8) for x in rs]
    return rs


# normalize sentence ranks with heuristics

def normalize_ranks(ranks):
    sranks = [(x, r) for (x, r) in ranks.items() if isinstance(x, int)]
    bias = forward_leaning(len(sranks))

    for ((x, r), b) in zip(sranks, bias):
        ranks[x] = r * b


def show(sequence):
    plt.plot(sequence)

    # Add labels and title to the plot
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Sequence Plot')

    # Display the plot
    plt.show()


def test_eureka():
    x = forward_leaning(100)
    y = forward_leaning(200)
    z = forward_leaning(400)

    for t in (x, y, z):
        print(t)
        print()
    show(y)


if __name__ == "__main__":
    test_eureka()
