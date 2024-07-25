#include "model.h"

DashCamModel::DashCamModel() : is_recording(false), clip_duration(3 * 60), storage_limit(1024 * 1024 * 1024) {
    video_quality.resolution = cv::Size(1920, 1080);
    video_quality.fps = 30;
    video_quality.bitrate = 1000000;
}

bool DashCamModel::start_recording() {
    if (!is_recording) {
        is_recording = true;
        return true;
    }
    return false;
}

bool DashCamModel::stop_recording() {
    if (is_recording) {
        is_recording = false;
        return true;
    }
    return false;
}

void DashCamModel::set_video_quality(int width, int height, int fps, int bitrate) {
    video_quality.resolution = cv::Size(width, height);
    video_quality.fps = fps;
    video_quality.bitrate = bitrate;
}

void DashCamModel::set_storage_limit(size_t limit) {
    storage_limit = limit;
}

std::string DashCamModel::get_status() const {
    // Implement JSON serialization here
    return "{}";
}