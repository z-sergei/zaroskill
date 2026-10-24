from invoice import total

for amount in (0, 1, 7, 100):
    result = total(amount)
    assert result == amount + 3
for amount in (-1, -20):
    rejected = False
    try:
        total(amount)
    except ValueError:
        rejected = True
    assert rejected
print('invoice checks passed')
