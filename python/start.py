s = {}

for i in range(4):
    n = input(f'Enter name{i+1}: ')
    l = input(f'Enter language{i+1}: ')
    
    original_n = n
    count = 1
    # Make sure the name is unique in the dictionary
    while n in s:
        n = f"{original_n}_{count}"
        count += 1
    
    s.update({n:l})

print(s)
