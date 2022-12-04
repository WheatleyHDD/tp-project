import main as mainProgram
import cProfile

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    mainProgram.start()

    pr.disable()
    pr.print_stats(sort="tottime")