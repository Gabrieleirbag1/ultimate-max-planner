CURRENT_DIR=$(pwd)

ng build --configuration=production

sudo cp .htaccess $CURRENT_DIR/dist/frontend/browser/

sudo cp -r $CURRENT_DIR/dist/frontend/* /var/www/ultimate-max-planner/