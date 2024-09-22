from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from db_utils import cursor, db
from datetime import datetime, timedelta
import vnpay

ve_chuyen_bay_routes = Blueprint('ve_chuyen_bay_routes', __name__)


@ve_chuyen_bay_routes.route('/ve_chuyen_bay/<ma_chuyen_bay>', methods=['GET', 'POST'])
def ve_chuyen_bay(ma_chuyen_bay):
    if request.method == 'GET':
        cursor.execute("SELECT * FROM ve_chuyen_bay WHERE ma_chuyen_bay = %s", (ma_chuyen_bay,))
        ve_chuyen_bay_list = cursor.fetchall()
        quyen = session['user']['vai_tro'] or 'Khách hàng'
        return render_template('ve_chuyen_bay.html', ve_chuyen_bay_list=ve_chuyen_bay_list, ma_chuyen_bay=ma_chuyen_bay,
                               quyen=quyen)


@ve_chuyen_bay_routes.route('/sua_ve_chuyen_bay/<ma_ve>', methods=['GET', 'POST'])
def sua_ve_chuyen_bay(ma_ve):
    if request.method == 'GET':
        # Lấy thông tin vé chuyến bay từ cơ sở dữ liệu
        cursor.execute("SELECT * FROM ve_chuyen_bay WHERE ma_ve = %s", (ma_ve,))
        flight_ticket = cursor.fetchone()
        quyen = session['user']['vai_tro'] or 'Khách hàng'
        if flight_ticket:
            return render_template('sua_ve_chuyen_bay.html', flight_ticket=flight_ticket, quyen=quyen)
        else:
            flash('Vé chuyến bay không tồn tại!')
            return redirect(url_for('ve_chuyen_bay_routes.ve_chuyen_bay', ma_chuyen_bay=flight_ticket[1]))

    elif request.method == 'POST':
        # Lấy thông tin từ form
        ma_ve = request.form['ma_ve']
        hang_ve_moi = request.form['hang_ve']
        gia_moi = request.form['gia']
        cursor.execute("SELECT * FROM ve_chuyen_bay WHERE ma_ve = %s", (ma_ve,))
        flight_ticket = cursor.fetchone()
        try:
            # Thực hiện cập nhật thông tin vé chuyến bay trong cơ sở dữ liệu
            cursor.execute("UPDATE ve_chuyen_bay SET hang_ve = %s, gia = %s WHERE ma_ve = %s",
                           (hang_ve_moi, gia_moi, ma_ve))
            db.commit()

            flash('Cập nhật vé chuyến bay thành công!')
            return redirect(url_for('ve_chuyen_bay_routes.ve_chuyen_bay', ma_chuyen_bay=flight_ticket[1]))

        except Exception as e:
            # Xử lý lỗi, ví dụ: log lỗi hoặc trả về một trang lỗi
            flash(f'Có lỗi xảy ra: {str(e)}')
            return redirect(url_for('ve_chuyen_bay_routes.ve_chuyen_bay', ma_chuyen_bay=flight_ticket[1]))
