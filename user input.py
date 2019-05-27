from datetime import datetime
import os
os.system('cls')
name = input("Enter a name: ")
while True:
  try:
    YOB = input("Enter your year of birth: ")
    age = datetime.utcnow().year - int(YOB)
    break #if it got here without throwing an exception, then it's a valid age, and we can continue on
  except:
    print("That didn't seem to be a valid number.")

print("Hello, "+name+"!")
print("You are "+str(age)+" years old this year!")
