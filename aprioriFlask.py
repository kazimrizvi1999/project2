from flask import Flask, request, render_template, redirect, url_for
import os
from itertools import combinations

app = Flask(__name__)

def find_frequent_1_itemsets(data, min_support):
    support_count = {}
    for transaction in data:
        for item in transaction:
            if item in support_count:
                support_count[item] += 1
            else:
                support_count[item] = 1

    frequent_1_itemsets = [{item} for item, count in support_count.items() if count >= min_support]
    return frequent_1_itemsets

def has_infrequent_subset(candidate, frequent_itemsets):
    k_minus_1_subsets = list(combinations(candidate, len(candidate) - 1))
    for subset in k_minus_1_subsets:
        if set(subset) not in frequent_itemsets:
            return True
    return False

def apriori_gen(frequent_itemsets, k):
    candidates = []
    len_frequent_itemsets = len(frequent_itemsets)
    for i in range(len_frequent_itemsets):
        for j in range(i + 1, len_frequent_itemsets):
            l1 = list(frequent_itemsets[i])
            l2 = list(frequent_itemsets[j])
            l1.sort()
            l2.sort()
            if l1[:k-2] == l2[:k-2]:
                candidate = frequent_itemsets[i] | frequent_itemsets[j]
                if not has_infrequent_subset(candidate, frequent_itemsets):
                    candidates.append(candidate)
    return candidates

def apriori(data, min_support):
    frequent_itemsets = []
    k = 1
    current_frequent_itemsets = find_frequent_1_itemsets(data, min_support)
    while current_frequent_itemsets:
        frequent_itemsets.extend(current_frequent_itemsets)
        k += 1
        candidates = apriori_gen(current_frequent_itemsets, k)

        support_count = {}
        for transaction in data:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    candidate = frozenset(candidate)
                    if candidate in support_count:
                        support_count[candidate] += 1
                    else:
                        support_count[candidate] = 1

        current_frequent_itemsets = [set(candidate) for candidate, count in support_count.items() if count >= min_support]

    return frequent_itemsets

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        min_support = int(request.form['min_support'])
        transactions = request.form['transactions'].splitlines()
        data = [set(transaction.split(',')) for transaction in transactions if transaction.strip()]

        results = apriori(data, min_support)
        return render_template('index.html', results=results, min_support=min_support)

    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)
