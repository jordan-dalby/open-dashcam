#include "presenter.h"
#include <spdlog/spdlog.h>
#include <filesystem>
#include <algorithm>

namespace fs = std::filesystem;

DashCamPresenter::DashCamPresenter(DashCamModel& model) : model(model), recordings_folder("recordings") {
    if (!fs::exists(recordings_folder)) {
        fs::create_directory(recordings_folder);
        spdlog::info("Created recordings folder: {}", recordings_folder);
    }
}

std::string DashCamPresenter::start_recording() {
    spdlog::debug("Received start recording request");
    if (model.start_recording()) {
        recording_thread = std::thread(&DashCamPresenter::record, this);
        return R"({"status": "Recording started"})";
    } else {
        return R"({"status": "Already recording"})";
    }
}

std::string DashCamPresenter::stop_recording() {
    spdlog::debug("Received stop recording request");
    if (model.stop_recording()) {
        if (recording_thread.joinable()) {
            recording_thread.join();
        }
        return R"({"status": "Recording stopped"})";
    } else {
        return R"({"status": "Not recording"})";
    }
}

std::string DashCamPresenter::get_status() {
    spdlog::debug("Received status request");
    return model.get_status();
}

std::string DashCamPresenter::set_quality(int width, int height, int fps, int bitrate) {
    spdlog::debug("Received set quality request");
    model.set_video_quality(width, height, fps, bitrate);
    return R"({"status": "Video quality updated"})";
}

std::string DashCamPresenter::set_storage_limit(size_t limit) {
    spdlog::debug("Received set storage limit request");
    model.set_storage_limit(limit);
    return R"({"status": "Storage limit updated"})";
}

void DashCamPresenter::record() {
    // Implement recording logic here
}

void DashCamPresenter::manage_storage() {
    // Implement storage management logic here
}