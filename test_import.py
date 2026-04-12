import sys
print("Python path:", sys.path)

try:
    import django
    print("Django version:", django.get_version())
except Exception as e:
    print("Django import error:", e)

try:
    from healthy import models
    print("Models imported successfully")
except Exception as e:
    print("Models import error:", e)
    import traceback
    traceback.print_exc()
