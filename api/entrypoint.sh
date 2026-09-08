#!/bin/sh
set -e

# Fix ownership of mounted directories at container startup.
# This is safe in both scenarios:
# - Standalone bind mounts (ownership comes from the host machine)
# - Compose named volumes (already correctly owned — this becomes a no-op)
chown -R appuser:appuser /app/uploaded_docs /app/chroma_db /app/local_db

# Drop root privileges and switch to appuser, then run the actual app command
exec gosu appuser "$@"