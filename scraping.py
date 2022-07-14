import pandas as pd
from libraries.browser import Browser

browser: Browser = Browser()
matches_df = pd.DataFrame(columns=['Date', 'Season', 'Score', 'Home/Away', 'Result', 'Opponent', 'Tournament'])

if __name__ == "__main__":
    try:
        browser.get(f"https://www.besoccer.com/team/matches/ca-rosario-central")
        browser.maximize_window()
        browser.close_pop_ups()
        matches_df = browser.create_seasons_df('//*[@id="season"]', 'SEASON 2010/11', matches_df)
        matches_df.to_csv('matches.csv', index=False)
    except:
        print('During the operation an error occured')
    finally:
        browser.close()

