<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>FLEETTRACKER AIRWAYS</title>
    <style>
        :root { --plane-silver: #e2e8f0; --sky-blue: #3182ce; --booked-red: #e53e3e; --hold-yellow: #ecc94b; }
        body { font-family: sans-serif; background: #1a202c; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; color: #2d3748; }
        .plane-fuselage { background: white; width: 380px; border-radius: 180px 180px 40px 40px; padding: 100px 30px 60px 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); position: relative; border: 8px solid var(--plane-silver); }
        .seat-grid { display: grid; grid-template-columns: repeat(3, 40px) 30px repeat(3, 40px); gap: 12px; justify-content: center; margin-top: 20px; }
        .seat { width: 38px; height: 42px; background: #f7fafc; border: 2px solid #cbd5e0; border-radius: 8px; cursor: pointer; font-size: 11px; display: flex; align-items: center; justify-content: center; }
        .seat.held { background: var(--hold-yellow); }
        .seat.booked { background: var(--booked-red); cursor: not-allowed; color: white; }
        .seat.selected { background: var(--sky-blue); color: white; }
        .aisle { width: 30px; }
        .booking-panel { position: fixed; right: 40px; width: 300px; background: white; padding: 25px; border-radius: 15px; border-top: 8px solid var(--sky-blue); }
        input { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .btn-pay { width: 100%; padding: 12px; background: var(--sky-blue); color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .hidden { display: none; }
    </style>
</head>
<body>

    <div class="plane-fuselage">
        <div id="grid" class="seat-grid"></div>
    </div>

    <div id="checkout-card" class="booking-panel hidden">
        <div id="timer" style="color:red; font-weight:bold; margin-bottom:10px;">05:00</div>
        <h3>Booking Details</h3>
        <p>Seat: <span id="seat-display"></span></p>
        <input type="text" id="full-name" placeholder="Full Name">
        <input type="email" id="email" placeholder="Email Address">
        <button class="btn-pay" id="pay-btn" onclick="finishBooking()">Book & Send PDF</button>
    </div>

    <script>
        let selectedSeats = [];
        let countdownInterval = null;

        async function refreshSeats() {
            const res = await fetch('/api/seats');
            const seats = await res.json();
            const grid = document.getElementById('grid');
            grid.innerHTML = '';
            seats.forEach((seat, index) => {
                const div = document.createElement('div');
                div.className = `seat ${seat.status} ${selectedSeats.includes(seat.seat_code) ? 'selected' : ''}`;
                div.innerText = seat.seat_code;
                if (seat.status === 'available') div.onclick = () => tryHoldSeat(seat.seat_code);
                grid.appendChild(div);
                if ((index + 1) % 6 === 3) { let a = document.createElement('div'); a.className = 'aisle'; grid.appendChild(a); }
            });
        }

        async function tryHoldSeat(code) {
            const res = await fetch('/api/hold', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({seat_code: code}) });
            const data = await res.json();
            if (data.success) {
                if (!selectedSeats.includes(code)) selectedSeats.push(code);
                document.getElementById('seat-display').innerText = selectedSeats.join(", ");
                document.getElementById('checkout-card').classList.remove('hidden');
                startCountdown(data.expiry);
                refreshSeats();
            }
        }

        async function finishBooking() {
            const name = document.getElementById('full-name').value;
            const email = document.getElementById('email').value;
            const btn = document.getElementById('pay-btn');

            if (!name || !email) return alert("Fill all fields");

            btn.disabled = true;
            btn.innerText = "Processing Boarding Pass...";

            for (const seat of selectedSeats) {
                await fetch('/api/book', { 
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'}, 
                    body: JSON.stringify({seat_code: seat, name, email}) 
                });
            }

            alert("Success! Check your email for the PDF.");
            resetUI();
        }

        function startCountdown(seconds) {
            if (countdownInterval) clearInterval(countdownInterval);
            countdownInterval = setInterval(() => {
                let m = Math.floor(seconds / 60), s = seconds % 60;
                document.getElementById('timer').innerText = `${m}:${s < 10 ? '0' : ''}${s}`;
                if (seconds-- <= 0) { clearInterval(countdownInterval); resetUI(); }
            }, 1000);
        }

        function resetUI() {
            selectedSeats = [];
            document.getElementById('checkout-card').classList.add('hidden');
            document.getElementById('pay-btn').disabled = false;
            document.getElementById('pay-btn').innerText = "Book & Send PDF";
            refreshSeats();
        }

        refreshSeats();
    </script>
</body>
</html>
