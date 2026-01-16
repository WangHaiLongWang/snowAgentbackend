from app import create_app
from app.db.models import Slope, db

app = create_app()

with app.app_context():
    # 更新所有雪道记录的image_url字段
    image_url = "http://115.159.78.59:8888/down/ZR1Ew6sSwhCI.jpg"
    slopes = Slope.query.all()
    
    for slope in slopes:
        slope.image_url = image_url
        db.session.add(slope)
    
    db.session.commit()
    print(f"Successfully updated {len(slopes)} slopes with image_url: {image_url}")
