f = '/home/student/labtainer/trunk/distrib/relabel.sh'
data = open(f).read().replace('--pull', '')
open(f, 'w').write(data)
print("Updated relabel.sh successfully!")
