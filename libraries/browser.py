import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import pandas as pd

class Browser(webdriver.Chrome):
    def __init__(self):
        super().__init__(executable_path='C:\Program Files (x86)\chromedriver.exe' ,options=webdriver.ChromeOptions().add_experimental_option('excludeSwitches', ['enable-logging']))

    def append_all_season_matches(self, element_xpath: str, matches_df: pd.DataFrame) -> pd.DataFrame:
        WebDriverWait(self, timeout=100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mod_detail_team_matches_off"]/div/a/div/div[1]')))
        self.find_element_by_xpath('//*[@id="mod_detail_team_matches_off"]/div/a/div/div[1]').click()
        WebDriverWait(self, timeout=100).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="mod_team_season_selector"]/div/div')))
        matches = self.find_element_by_xpath(element_xpath)
        select = Select(self.find_element_by_xpath('//*[@id="season"]'))
        season = select.first_selected_option.text
        WebDriverWait(self, timeout=100).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.match-link')))
        for match in matches.find_elements_by_css_selector('a.match-link'):
            date = match.find_element_by_class_name('date').text
            score = match.find_element_by_class_name('marker').text
            team_left = match.find_element_by_class_name('team_left').text
            team_right = match.find_element_by_class_name('team_right').text
            tournament = match.find_element_by_class_name('middle-info').text

            if(team_left=='Rosario Central'):
                bool_home = True
            else:
                bool_home = False
            if(bool_home):
                opponent = team_right
                home_away = 'Home'
            else:
                opponent = team_left
                home_away = 'Away'
                score = score[::-1]

            result = self.get_result(score, home_away)
            new_row = pd.DataFrame([{'Date': date, 'Season': season, 'Score': score, 'Home/Away': home_away, 'Result': result, 'Opponent': opponent, 'Tournament': tournament}])
            matches_df = pd.concat([matches_df, new_row], axis=0, ignore_index=True)
        return matches_df

    def close_pop_ups(self) -> None:
        try:
            WebDriverWait(self, timeout=50).until(EC.presence_of_element_located((By.XPATH, '//*[@id="team"]/div[5]')))
            self.execute_script('''return document.querySelector('div.grv-dialog-host').shadowRoot.querySelector('div#grv-popup div.grv-popup__block div.grv-popup__inner div.grv-popup__content div.block')''').click()
            self.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]').click()
        except:
            print("Couldn't found this pop up")
            self.close()

    def create_seasons_df(self, select_xpath: str, last_season: str, matches_df: pd.DataFrame) -> pd.DataFrame:
        select = Select(self.find_element_by_xpath(select_xpath))
        options = select.options
        for index in range(0, len(options)):
            if(select.options[index].text != last_season):
                select.select_by_index(index)
                matches_df = self.append_all_season_matches('//*[@id="mod_detail_team_matches_off"]', matches_df)
                WebDriverWait(self, timeout=50).until(EC.presence_of_element_located((By.XPATH, select_xpath)))
                select = Select(self.find_element_by_xpath(select_xpath))
            else:
                return matches_df

    def get_result(self, score: str, home_away: str) -> str:
        try:
            own_score = int(score.split("-")[0])
            opponent_score = int(score.split("-")[1])
            penalties_bool = False
        except:
            own_score = int(score.split(" ")[0])
            opponent_score = int(score.split(" ")[2])
            penalties = score.split(" ")[1].replace('(',' ').replace(')', '')
            if(home_away=='Away'):
                penalties = penalties[::-1]
            own_penalties = int(penalties.split("-")[0])
            opponent_penalties = int(penalties.split("-")[1])
            penalties_bool = True

        if(opponent_score==own_score and not penalties_bool):
            result = 'Draw'
        elif(own_score > opponent_score):
            result = 'Win'
        elif(own_score < opponent_score):
            result = 'Lose'
        elif(penalties_bool and own_penalties > opponent_penalties):
            result = 'Win'
        elif(penalties_bool and own_penalties < opponent_penalties):
            result = 'Lose'
        return result