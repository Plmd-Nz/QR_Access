from sqlite3 import SQLITE_NOMEM
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

hashed = bcrypt.generate_password_hash("admin_password").decode('utf-8')
print(hashed)

from PIL import Image
from rembg import remove

inp=Image.open("input.png")
output = remove(inp)
output.save("out.png")
