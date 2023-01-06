
# Bytes -> KB MB GB
def trans_B2KB(val):
    return float(val) / 1024


def trans_B2MB(val):
    return trans_B2KB(val)/1024


def trans_B2GB(val):
    return trans_B2MB(val)/1024
