import subprocess

def mvn_package(logger) -> bool:
    try:
        logger.info("Running mvn -q -DskipTests package")
        subprocess.check_call(["mvn", "-q", "-DskipTests", "package"])
        logger.info("Build OK")
        return True
    except subprocess.CalledProcessError:
        logger.info("Build FAILED")
        return False
