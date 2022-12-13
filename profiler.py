import main as mainProgram
import cProfile
import vacancies
import statistics
import year_splitter
import mp_stats
import conc_stats

if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    conc_stats.InputConnect("chunks", "Аналитик")
    # mp_stats.InputConnect("chunks", "Аналитик")
    # statistics.InputConnect("vacancies.csv", "Аналитик")

    pr.disable()
    pr.print_stats(sort="tottime")