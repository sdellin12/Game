import unittest
from unittest.mock import patch
from crucible_play.desktop import main


class PlayLauncherTests(unittest.TestCase):
    def test_human_lobby_starts_without_bot_actions_or_dealing(self):
        for count in (2,3,4):
            with patch('crucible_play.desktop.tk.Tk') as root,patch('crucible_play.desktop.PlayWindow') as window:
                main(['--hotseat','--players',str(count)])
            session=window.call_args.args[1]
            self.assertEqual(len(session.view()['players']),count);self.assertFalse(session.bots)
            self.assertEqual(session.view()['phase'],'lobby');self.assertFalse(session._lobby.opening)
            root.return_value.mainloop.assert_called_once()

    def test_default_and_package_launch_keep_correct_computer_seats(self):
        for args,expected in (([], 'crucible-practice'),(['--discard-package','--players','4'],'crucible-discard-draw')):
            with patch('crucible_play.desktop.tk.Tk'),patch('crucible_play.desktop.PlayWindow') as window:main(args)
            session=window.call_args.args[1]
            self.assertEqual(session._lobby.pack.pack_id,expected)
            self.assertEqual(session.bots,frozenset(f'P{i+1}' for i in range(1,len(session.view()['players']))))
