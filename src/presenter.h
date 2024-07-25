#pragma once
#include <string>
#include <thread>
#include "model.h"

class DashCamPresenter {
public:
    DashCamPresenter(DashCamModel& model);
    std::string start_recording();
    std::string stop_recording();
    std::string get_status();
    std::string set_quality(int width, int height, int fps, int bitrate);
    std::string set_storage_limit(size_t limit);

private:
    void record();
    void manage_storage();

    DashCamModel& model;
    std::thread recording_thread;
    std::string recordings_folder;
};