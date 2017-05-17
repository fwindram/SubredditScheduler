# queuebuilder.py
# Skeletorfw
# 17/05/17
#
# Python 3.4.1
#
# An easy way to add to the SSched queue:

import csv
import cmd


class BuilderShell(cmd.Cmd):
    intro = 'Welcome to the queue builder. You can use this to quickly build entries for the SSched queue.\n' \
            'Type help or ? to list commands.\n'
    prompt = '(builder)'
    cwe = ['', '', '']
    cwe_default = ['', '', '']
    staged = []
    # Command list

    def do_url(self, arg):
        """Change URL field on current working entry:   url http://www.youtube.com/lasdjfkaljdflkj"""
        self.cwe[0] = arg

    def do_title(self, arg):
        """Change Title field on current working entry: title 'This is the title of the post.'"""
        self.cwe[1] = arg

    def do_sr(self, arg):
        """Change Subreddit field on current working entry: sr AskReddit"""
        self.cwe[2] = arg

    def do_sr_default(self, arg):
        """Change default Subreddit field (also changes CWE sr field): sr_default AskReddit"""
        self.cwe[2] = arg
        self.cwe_default[2] = arg

    def do_commit(self, arg):
        """Commit current working entry to stage and reinitialise working entry as default:    commit"""
        if self.cwe[0] == '' or self.cwe[1] == '':
            print("Entry must have both a title and a url!\n")
        else:
            if self.cwe[2] == '':
                del self.cwe[2]
            self.staged.append(self.cwe)
            self.cwe = list(self.cwe_default)

    def do_print(self, arg):
        """Print current working entry to screen:   print"""
        print("{0:>9}: {1}".format("URL", self.cwe[0]))
        print("{0:>9}: {1}".format("Title", self.cwe[1]))
        print("{0:>9}: {1}\n".format("Subreddit", self.cwe[2]))

    def do_cwe(self, arg):
        """Print current working entry to screen:   cwe"""
        self.do_print(arg)

    def do_list(self, arg):
        """Print staged queue to screen.    list"""
        i = 0
        print("Currently Staged:")
        if len(self.staged) < 1:
            print("None.")
        else:
            for x in self.staged:
                if len(x) == 2:
                    print("{0:3}: {1}|{2}".format(i, x[0], x[1]))
                else:
                    print("{0:3}: {1}|{2}|{3}".format(i, x[0], x[1], x[2]))
                i += 1
        print()

    def do_edit(self, arg):
        """Pull entry from staged queue to current working entry:  edit 1"""
        try:
            arg = int(arg)
            try:
                self.cwe = self.staged.pop(arg)
            except IndexError:
                print("Entry {0} does not exist in the staged queue.\n")
        except TypeError:
            print("Edit argument must be an integer\n")

    def do_save(self, arg):
        """Write from staged queue to subqueue.csv and clear queue, current working entry & defaults:    save"""
        print("Saving queue to subqueue.csv...")
        with open("../data/subqueue.csv", "a", newline='') as queuefile:
            queuewriter = csv.writer(queuefile, delimiter='|')
            queuewriter.writerows(self.staged)
        print("Clearing queue and CWE...\n")
        self.do_reset(arg)

    def do_reset(self, arg):
        """Delete staged queue, current working entry and reset all defaults:   reset"""
        self.cwe_default = ['', '', '']
        self.cwe = list(self.cwe_default)
        self.staged = []

    def do_exit(self, arg):
        """Exit BuilderShell:   exit"""
        print("Exiting...")
        return True

    def do_dump(self, arg):
        """Print all current internal variables straight out for debugging purposes:   dump"""
        print("CWE: {0}".format(self.cwe))
        print("CWE DEFAULT: {0}".format(self.cwe_default))
        print("STAGE: {0}\n".format(self.staged))
    # Alternative commands

    def do_clear(self, arg):
        """Clear current working entry to default to start again:  clear"""
        self.cwe = list(self.cwe_default)

    def do_ll(self, arg):
        """Print staged queue to screen.    ll"""
        self.do_list(arg)

if __name__ == '__main__':
    BuilderShell().cmdloop()
