#!/bin/sh

cd `readlink -f .`/src
rm go-backup.zip
zip -r ../go-backup.zip *
cd ..
echo '#!/usr/bin/env python' | cat - go-backup.zip > go-backup
rm go-backup.zip
chmod +x go-backup
