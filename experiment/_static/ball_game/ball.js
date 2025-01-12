class Ball {
    constructor(speed, acceleration, size, bg_color, border_color, lane_width, n_lanes, game_height, active, draw_smiley = false) {
        this.base_speed = speed;
        this.size = size;
        this.acceleration = acceleration;
        this.bg_color = bg_color;
        this.border_color = border_color;
        this.lane_width = lane_width;
        this.n_lanes = n_lanes;
        this.active = active;
        this.game_height = game_height;
        this.draw_smiley = draw_smiley;

        this.lane = 0;
        this.rotation = 0;  // Current rotation angle
        this.spin_speed = 0;  // Will be set randomly when spawned

        this.x = this.lane * this.lane_width + this.lane_width / 2;
        this.y = 0;
    }

    drawSmileyFace() {
        // Scale features based on ball size
        let scale = this.size / 100;

        // Draw eyes
        fill(0);
        noStroke();
        circle(-15 * scale, -10 * scale, 10 * scale);
        circle(15 * scale, -10 * scale, 10 * scale);

        // Draw smile
        noFill();
        stroke(color(this.border_color));
        strokeWeight(2 * scale);
        arc(0, 5, 40 * scale, 40 * scale, 0, PI);
        strokeWeight(1);
    }

    render() {
        if (this.active) {
            // Update the speed by the acceleration
            this.speed = this.speed * this.acceleration;

            // Update the balls position
            this.y = this.y + this.speed;

            // Update rotation
            this.rotation += this.spin_speed;

            // If the ball left the screen, set it to inactive
            if (this.y > this.game_height + this.size / 2) {
                this.active = false;
            }

            push();  // Save current transformation state
            translate(this.x, this.y);
            rotate(this.rotation);

            // Draw the main circle
            fill(color(this.bg_color));
            stroke(color(this.border_color));
            circle(0, 0, this.size);

            // Draw smiley face if enabled
            if (this.draw_smiley) {
                this.drawSmileyFace();
            }

            pop();  // Restore transformation state
        }
    }

    spawn_in_lane(lane) {
        this.lane = lane;
        this.active = true;
        this.y = -1 - this.size / 2;
        this.x = this.lane * this.lane_width + this.lane_width / 2;
        this.speed = this.base_speed;

        // Set random spin speed between -0.05 and 0.05 radians per frame
        this.spin_speed = random(-0.05, 0.05);
        // Reset rotation to random starting angle
        this.rotation = random(TWO_PI);
    }

    is_active() {
        return this.active;
    }

    set_active(active) {
        this.active = active;
    }

    get_lower_edge() {
        return this.y + this.size / 2;
    }
}