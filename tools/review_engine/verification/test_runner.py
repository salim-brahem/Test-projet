import subprocess

def mvn_test(logger) -> bool:
    try:
        logger.info("Running mvn -q test")
        subprocess.check_call(["mvn", "-q", "test"])
        logger.info("Tests OK")
        return True
    except subprocess.CalledProcessError:
        logger.info("Tests FAILED")
        return False
