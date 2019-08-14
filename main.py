from settings import MODE

if MODE == 'SEND':
    from send_main import main
elif MODE == 'RECV':
    from recv_main import main
elif MODE == 'DEBUG':
    from debug import main
else:
    def main():
        print("INVALID START MODE")

main()
