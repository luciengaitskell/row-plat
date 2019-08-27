from settings import MODE

if MODE == 'BOAT':
    from boat_main import main
elif MODE == 'CTRL':
    from ctrl_main import main
elif MODE == 'DEBUG':
    from debug import main
else:
    def main():
        print("INVALID START MODE")

main()
