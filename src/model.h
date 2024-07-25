#pragma once
#include <atomic>
#include <opencv2/opencv.hpp>

class DashCamModel {
public:
    DashCamModel();
    bool start_recording();
    bool stop_recording();
    void set_video_quality(int width, int height, int fps, int bitrate);
    void set_storage_limit(size_t limit);
    std::string get_status() const;

private:
    std::atomic<bool> is_recording;
    cv::VideoCapture camera;
    cv::VideoWriter output;
    int clip_duration;
    size_t storage_limit;
    struct {
        cv::Size resolution;
        int fps;
        int bitrate;
    } video_quality;
};