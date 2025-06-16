import yaml
import bcrypt

password = "$$$$$$$$$"  # not real password))
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

with open("passwords.yaml", "w") as file:
    yaml.dump({"hashed_password": hashed_password}, file)
