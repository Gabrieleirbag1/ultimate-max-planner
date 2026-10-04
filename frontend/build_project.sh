CURRENT_DIR=$(pwd)

ng build --configuration=production

sudo cp .htaccess $CURRENT_DIR/dist/ultimate-max-planner/browser/

sudo cp -r $CURRENT_DIR/dist/ultimate-max-planner/* /var/www/ultimate-max-planner/