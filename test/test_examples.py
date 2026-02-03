import pytest

def test_pass():
    # Denne test vil passere
    assert 1 + 1 == 2


def test_fail():
    # Denne test vil fejle
    assert 1 * 1 == 3


@pytest.mark.skip(reason="Springes over med vilje") # Denne test bliver slet ikke kørt
def test_skip():
    assert False # failed test bliver ignoreret
    raise RuntimeError("Test crashede med vilje") # crash bliver også ignoreret


def test_crash():
    # Denne test crasher med en exception
    raise RuntimeError("Test crashede med vilje")


    assert False # failed test bliver ignoreret
# 1. PASS: Test af string manipulation
def test_string_formatting_pass():
    skole = "zealand"
    # Denne test passerer, fordi metoden .upper() gør teksten til store bogstaver
    assert skole.upper() == "ZEALAND"


# 2. FAIL: Test af liste indhold
def test_list_content_fail():
    byer = ["Næstved", "Slagelse", "Roskilde"]
    # Denne test fejler, fordi "København" ikke er i listen
    assert "København" in byer


# 3. SKIP: Test der springes over (f.eks. en funktion der ikke er færdig)
@pytest.mark.skip(reason="Denne funktion er under udvikling")
def test_feature_under_development_skip():
    # Denne assertion bliver aldrig tjekket
    assert 5 * 5 == 0


# 4. CRASH: Test der crasher på grund af en kodefejl (ZeroDivisionError)
def test_math_crash():
    nummer = 100
    # Denne test crasher øjeblikkeligt, fordi man ikke kan dividere med 0 i Python
    resultat = nummer / 0
    
    assert resultat == 100