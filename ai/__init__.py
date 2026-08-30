# Makes "ai" importable as a package, e.g.:
#     from ai.services.feedback_analyzer import analyze_feedback
#
# This file is intentionally empty of logic. Anything imported here
# runs the moment ANY submodule of "ai" is imported, so keeping it
# empty avoids surprise side effects (like loading a model) just
# because the backend imported one small function.
