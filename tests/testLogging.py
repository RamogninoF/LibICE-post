from libICEpost.src.base.Logging.Logging import logger, usrLogger, devLogger, set_debug_level

usrLogger().info("Info for usr")
usrLogger().debug("debug for usr")
usrLogger().error("error for usr")
devLogger().info("Info for dev")

devLogger().info("SecondInfo for dev")

testLogger = devLogger.getLogger("test", switch=True)
testLogger().info("TEST")

set_debug_level(2)
testLogger().info("TEST")