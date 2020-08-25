import pandas as pd
import pygsheets
import sys
import datetime
import time
import curses

top_300_file = 'top300.csv'
team_rank = 'team_rank.csv'
service_file = 'sa.json'

def csv_to_df(file_name):
    """pull top ranked players into df"""
    df = pd.read_csv(file_name)
    return df

def gsheet_api_to_df():
    """Connect to Fantasy Draft, pull Available Players and return df"""
    gc = pygsheets.authorize(service_file=service_file)
    sh = gc.open("2020 Fantasy Draft")
    wks = sh.worksheet_by_title("AvailablePlayers")
    cell_matrix = wks.get_all_values(returnas='matrix')
    df = pd.DataFrame(cell_matrix)

    #only grab relevant columns
    df = df.iloc[:,0:5]

    #make header row header and remove that false data row from data set
    df.columns = df.iloc[0]
    df = df.iloc[1:]

    return df

def df_magic(player_rank_df,team_rank_df,player_draft_status_df):
    """Merge data and output top 3 remaining players of each position, ordered by Team Rank
    To Do:  Can insert custom ranking mechanism, ML Model, whatever here later"""
    #join player rank to team rank df
    player_team_rank_df = pd.merge(player_rank_df,team_rank_df, how='left', on=['Team'])

    #join resulting df to remaining players
    mother_load_df = pd.merge(player_team_rank_df,player_draft_status_df,how='left',on=['Player'])
    #filter by available players
    mother_load_df = mother_load_df.loc[mother_load_df['Status'] == "Available"]
    #data cleanup work
    mother_load_df.rename(columns={'Rank_x': 'Player_Rank', 'Rank_y': 'Team_Rank',
                                   'Team_x': 'Team', 'Position_x':'Position'}, inplace=True)
    mother_load_df = mother_load_df.drop(['Rank', 'Team_y', 'Position_y'], axis=1)
    mother_load_df['Team_Rank'] = mother_load_df['Team_Rank'].fillna(0.0).astype(int)
    #ranked, grouped by position
    mother_load_df = mother_load_df.groupby('Position').head(3)

    return mother_load_df

def main():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()

    """Take ESPN top 300, take team ranks(manually loaded), and available players
    Return a list of choices, choices, choices..."""
    player_rank_df = csv_to_df(top_300_file)
    team_rank_df = csv_to_df(team_rank)

    try:
        while True:
            player_draft_status_df = gsheet_api_to_df()

            choices_choices = df_magic(player_rank_df,team_rank_df,player_draft_status_df)

            stdscr.addstr(0, 0, str(datetime.datetime.now()))
            stdscr.addstr(1, 0, str(choices_choices))
            stdscr.refresh()
            time.sleep(5)
    finally:
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    # player_draft_status_df = gsheet_api_to_df()
    #
    # choices_choices = df_magic(player_rank_df,team_rank_df,player_draft_status_df)
    # print (choices_choices)

if __name__ == "__main__":
    main()
