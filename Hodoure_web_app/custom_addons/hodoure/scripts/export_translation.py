import random 

password = ''.join(random.choice('0123456789') for i in range(6))

print(password)