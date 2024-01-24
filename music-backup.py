
# MAKE SURE YOU ARE ABLE TO run 'python run_first_test.py' successfully, see the file in question for details.

if __name__ == "__main__":
    from gui.gui import MainGUI
    from api import api as SpotipyAPI
    MainGUI(SpotipyAPI.SpotipyAPI)
