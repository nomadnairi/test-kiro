"""Username extraction from NL goals + social-profile parsing."""
import pytest

from deathbot.tools.investigator import AIInvestigator, _USERNAME_TOOLS
from deathbot.tools.investigation import Investigation


@pytest.mark.parametrize("goal,expected", [
    ("проверь ник death gun, а потом посмотри поочередно", "death gun"),
    ("найди логин @vasya и скажи", "vasya"),
    ("проверь юзернейм john_doe", "john_doe"),
    ("проверь аккаунт test.user.99", "test.user.99"),
])
def test_extract_username(goal, expected):
    assert AIInvestigator.extract_username(goal) == expected


def test_plain_handle_untouched():
    assert AIInvestigator.extract_username("deathgun") == "deathgun"


@pytest.mark.asyncio
async def test_sherlock_profiles_become_social_accounts():
    """H2 regression: sherlock output '[+] Site: https://…' must produce
    social_account findings — the report used to show only counts."""
    inv = Investigation(chat_id=1, user_id=2, goal="u",
                        root_target="death gun")
    sherlock_out = (
        "[+] BoardGameGeek: https://boardgamegeek.com/user/death%20gun\n"
        "[+] Codeforces: https://codeforces.com/profile/death%20gun\n"
        "[+] Discord: https://discord.com\n")
    from deathbot.tools.investigator import _extract_entities
    _extract_entities(inv, "sherlock_cli", sherlock_out,
                      related_to="death gun")
    socials = [f for f in inv.findings if f.kind == "social_account"]
    hosts = {f.value for f in socials}
    assert "boardgamegeek.com" in hosts
    assert "codeforces.com" in hosts
    # discord.com root URL is noise (no profile path) — still captured but
    # that's acceptable; the key assertion is real profiles got through.


def test_noise_hosts_filtered():
    from deathbot.tools.investigator import _NOISE_HOSTS
    assert "github.com" in _NOISE_HOSTS
