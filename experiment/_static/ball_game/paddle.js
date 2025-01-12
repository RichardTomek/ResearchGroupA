class Paddle {
    constructor(width, height, y_offset, bg_color, border_color, lane_width, game_width, game_height, n_lanes) {
        this.width = width;
        this.height = height;
        this.y_offset = y_offset;
        this.bg_color = bg_color;
        this.border_color = border_color;
        this.lane_width = lane_width;
        this.game_width = game_width;
        this.game_height = game_height;
        this.n_lanes = n_lanes;

        // In the beginning, set the x position of the paddle to the left most lane
        this.x = 0;
        this.current_lane = 0;
    }

    render() {
        fill(color(this.bg_color));
        stroke(color(this.border_color));

        this.x = this.current_lane * lane_width + (lane_width - this.width) / 2;
        rect(this.x, this.game_height - this.y_offset - this.height, this.width, this.height);

    }

    // Jump one lane. If +1 to the right, if -1 to the left
    move_lane(dir) {
        this.current_lane += dir;
        if (this.current_lane < 0) {
            this.current_lane = 0;
        } else if (this.current_lane >= n_lanes) {
            this.current_lane = n_lanes - 1;
        }
    }

    get_upper_edge() {
        return this.game_height - this.y_offset - this.height;
    }

    get_lower_edge() {
        return this.game_height - this.y_offset;
    }
}