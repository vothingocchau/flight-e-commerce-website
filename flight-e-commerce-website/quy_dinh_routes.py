from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from db_utils import cursor, db
from datetime import datetime, timedelta
import vnpay

quy_dinh_routes = Blueprint('quy_dinh_routes', __name__)


@quy_dinh_routes.route('/doanh_thu_theo_thang', methods=['GET', 'POST'])
def doanh_thu_theo_thang():
    if request.method == 'POST':
        # Lấy tháng từ yêu cầu POST
        selected_month = int(request.form['selected_month'].split("-")[1])
    else:
        quyen = session['user']['vai_tro'] or 'Khách hàng'
        # Lấy tháng từ yêu cầu GET hoặc thiết lập giá trị mặc định
        return render_template('doanh_thu_theo_thang.html', quyen=quyen)

    try:
        # Thực hiện truy vấn SQL để lấy dữ liệu doanh thu theo tháng
        query = """
            SELECT chuyen_bay.san_bay_di, chuyen_bay.san_bay_den,
                   SUM(ve_chuyen_bay.gia) AS doanh_thu, COUNT(*) AS so_luot_bay
            FROM ve_chuyen_bay
            JOIN chuyen_bay ON ve_chuyen_bay.ma_chuyen_bay = chuyen_bay.ma_chuyen_bay
            JOIN dat_ve_chuyen_bay ON ve_chuyen_bay.ma_ve = dat_ve_chuyen_bay.ma_ve
            WHERE MONTH(dat_ve_chuyen_bay.thoi_diem_dat_ve) = %s
            GROUP BY chuyen_bay.san_bay_di, chuyen_bay.san_bay_den
        """

        cursor.execute(query, (selected_month,))
        result = cursor.fetchall()

        # Chuẩn bị dữ liệu cho biểu đồ
        labels = [f"{row[0]} - {row[1]}" for row in result]
        data = [int(row[2]) for row in result]

        # Tính tổng doanh thu
        total_revenue = sum(data)

        # Tính tỷ lệ doanh thu
        percentages = [int((revenue / total_revenue) * 100) for revenue in data]
        print(data)
        print(percentages)
        print(total_revenue)
        # Chuẩn bị dữ liệu để trả về dưới dạng JSON
        chart_data = {
            'labels': labels,
            'data': data,
            'percentages': percentages,
            'total_revenue': total_revenue
        }

        return jsonify(chart_data)

    except Exception as e:
        # Handle the exception, e.g., log it or return an error response
        return jsonify({'error': str(e)})


@quy_dinh_routes.route('/thay_doi_quy_dinh', methods=['GET', 'POST'])
def thay_doi_quy_dinh():
    if request.method == 'GET':
        # Lấy thông tin quy định hiện tại từ cơ sở dữ liệu
        cursor.execute("SELECT * FROM quy_dinh")
        quy_dinh = cursor.fetchone()
        quyen = session['user']['vai_tro'] or 'Khách hàng'
        return render_template('thay_doi_quy_dinh.html', quy_dinh=quy_dinh, quyen=quyen)

    elif request.method == 'POST':
        # Lấy thông tin từ form
        so_luong_san_bay = int(request.form['so_luong_san_bay'])
        thoi_gian_bay_toi_thieu = int(request.form['thoi_gian_bay_toi_thieu'])
        so_san_bay_trung_gian_toi_da = int(request.form['so_san_bay_trung_gian_toi_da'])
        thoi_gian_dung_toi_thieu = int(request.form['thoi_gian_dung_toi_thieu'])
        thoi_gian_dung_toi_da = int(request.form['thoi_gian_dung_toi_da'])
        so_gio_dat_ve_truoc = int(request.form['so_gio_dat_ve_truoc'])
        so_gio_ban_ve_truoc = int(request.form['so_gio_ban_ve_truoc'])

        try:
            # Thực hiện cập nhật quy định trong cơ sở dữ liệu
            cursor.execute("UPDATE quy_dinh SET so_luong_san_bay = %s, thoi_gian_bay_toi_thieu = %s, "
                           "so_san_bay_trung_gian_toi_da = %s, thoi_gian_dung_toi_thieu = %s, "
                           "thoi_gian_dung_toi_da = %s, so_gio_dat_ve_truoc = %s, so_gio_ban_ve_truoc = %s WHERE ma_quy_dinh = 1",
                           (so_luong_san_bay, thoi_gian_bay_toi_thieu, so_san_bay_trung_gian_toi_da,
                            thoi_gian_dung_toi_thieu, thoi_gian_dung_toi_da, so_gio_dat_ve_truoc, so_gio_ban_ve_truoc))
            db.commit()

            flash('Cập nhật quy định thành công!')
            return redirect(url_for('quy_dinh_routes.thay_doi_quy_dinh'))

        except Exception as e:
            # Xử lý lỗi, ví dụ: log lỗi hoặc trả về một trang lỗi
            flash(f'Có lỗi xảy ra: {str(e)}')
            return redirect(url_for('quy_dinh_routes.thay_doi_quy_dinh'))

