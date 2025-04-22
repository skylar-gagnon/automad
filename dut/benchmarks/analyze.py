import os

def main():
    dir_path = 'measurements/10s'
    for bench in os.listdir(dir_path):
        with open(f'{dir_path}/{bench}', 'r') as f:
            results = f.read()

        currs = [int(r) for r in results if r.strip()]
        max_p2p = 0
        avg_p2p = 0.0
        prev_curr = currs[0]
        for curr in currs[1:]:
            p2p = abs(prev_curr - curr)
            if p2p > max_p2p: max_p2p = p2p
            avg_p2p += p2p
            prev_curr = curr

        avg_p2p = avg_p2p / float(len(currs) - 1)
        print(f"{bench}:\n\tAvg: {avg_p2p}\n\tMax: {max_p2p}")

if __name__ == '__main__':
    main()