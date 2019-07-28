from settings import MODE

if MODE == 'SEND':
    import send_main
elif MODE == 'RECV':
    import recv_main
elif MODE == 'DEBUG':
    import debug
else:
    print("INVALID START MODE")
