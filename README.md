
# Font Selector

This is a simple project which made it easier to select fonts for CNC and laser engraving projects.

## Getting started

In the below if your default 'python' is python3 then change the below commands to just be 'python'.

1. Ubuntu: Install necessary prerequisites
   ```
   sudo apt install -y python3
   python3 -m pip install --user --upgrade pip
   python3 -m pip install --user virtualenv
   ```
   In Ubuntu to allow PyQT - along with QtCreator - to work do:
   ```
   sudo apt-get update -y
   sudo apt-get install libxcb-icccm4 libxcb-xkb1 libxcb-icccm4 libxcb-image0 libxcb-render-util0 libxcb-randr0 libxcb-keysyms1 libxcb-xinerama0
   sudo apt-get install qtcreator qt5-default qt5-doc qtbase5-examples qt5-doc-html qtbase5-doc-html
   ```
1. Windows:  It is useful to use QtDesigner which can be downloaded from https://build-system.fman.io/qt-designer-download.

1. Create a new virtual environment within the same directory as the git checkout.
   ```
   cd FontSelector
   python3 -m virtualenv --python=python3 env
   ```
1. Activate the new virtual environment
   ```
   source env/bin/activate
   ```
   or 
   ```
   env\scripts\activate.bat
   ```
   if you are on windows.
1. Install, into the new virtual environment, the required python modules for this specific environment.  This will be installed within the virtual env which was activated earlier.
   ```
   python3 -m pip install -r requirements.txt
   ```

   Then you can just run 
   ```
   python3 PixelArt.py
   ```

## Additional
There is no real documentation here beyond the code.  IF necessary then I will augment at some future date.

1. Install necessary prerequisites
   ```
   sudo apt install -y python3
   python3 -m pip install --user --upgrade pip
   python3 -m pip install --user virtualenv
   ```
1. Create a new virtual environment within the same directory as the git checkout.
   ```
   cd ScheduleEventHelper
   python3 -m virtualenv --python=python3 seh-env
   ```
1. Activate the new virtual environment
   ```
   source seh-env/bin/activate
   ```
1. Install, into the new virtual environment, the required python modules for this specific environment.  This will be installed within the virtual env which was activated earlier.
   ```
   python3 -m pip install -r requirements.txt
   ```
1. Start Jupyter-lab
   ```
   jupyter-lab
   ```
1. Navigate to the Jupyter notebook checked in here.

# Rules

1. Every team needs a goalkeeper and is placed first.  The number of goal keepers determines the number of teams.
1. All teams have to have the same number of players.  For configurations where this is not possible then no team should have more than 1 member for the smallest team.
1. As much as possible there must be a good distribution of skill across the teams.  This is captured using the skill numeric value (SNV) within the input spreadsheet.  
1. A good distribution of skill does not allow for one team with many highly skilled (3) players and then a few lower skilled (1) players to given it an overall balance.  Many highly skilled players working together are better than average players.
1. Given the overall makeup of a team we next need the right assignment of positions.  If the teams were 8 people then, as an example, we would want: 3 Midfield, 3 Defense, 2 offense.
1. There was a specific request to ensure that Mindy Au be on the team with Maha.

# Team assignments

There are two things that we are trying to balance.  First, each team has to have the same number of people.  
Given certain numbers of players and teams we will, of course, have some teams with one more player than the
minimum.  But we must have the same number of players.  This is paramount.  

Now that the team sizes are the same we want to minimize the difference between the maximum and minimum skill
level across all teams.  

I used the following algorithm.

* For each player to assign to a team:
   * Find all teams with the minimum number of players
   * For each one of these pretend that we were to assign the new player
   * Evaluate the overall min and max total skill level if we made this assignment
   * Choose the best assignment that minimizes the distance between total skill of all teams.

This worked very well in practice.
