import os
import re
import sublime
import sublime_plugin
import subprocess

# TODO actually check if a line was added or deleted
# TODO run automatically on save
class GitLineStatusCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.view.erase_regions('git-line-status-added')
    self.view.erase_regions('git-line-status-deleted')

    directory = self.view.window().extract_variables()['folder']

    os.chdir(directory)

    hunk_regex = r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))?\ @@'

    try:
      output = subprocess.check_output([
        'git',
        'diff',
        '-U0', # 0 lines of context as we only care about changed lines
        '--no-color',
        self.view.file_name()
      ]).decode()

      for line in output.split('\n'):
        print(line)
        is_hunk = match = re.search(hunk_regex, line)

        if is_hunk:
          print('at line number "', match.group(1), '" added "', match.group(2), '" lines')
          self.added(
            int(match.group(1)) - 1,
            int(match.group(2))
          )
    except subprocess.CalledProcessError as error:
      print('OH NO!!!!!', error.returncode)
      print(error.output)

  def added(self, first_line, number_of_lines):
    regions = []

    for line_number in range(first_line, first_line + number_of_lines):
      point = self.view.text_point(line_number, 0)
      regions.append(self.view.line(point))

    self.view.add_regions(
      'git-line-status-added',
      regions + self.view.get_regions('git-line-status-added'),
      'markup.inserted',
      'dot',
      sublime.HIDDEN | sublime.PERSISTENT
    )
