#include "view.h"
#include <nlohmann/json.hpp>

DashCamView::DashCamView(DashCamPresenter& presenter) : presenter(presenter) {
    setup_routes();
}

void DashCamView::setup_routes() {
    server.Post("/start", [this](const httplib::Request&, httplib::Response& res) {
        res.set_content(presenter.start_recording(), "application/json");
    });

    server.Post("/stop", [this](const httplib::Request&, httplib::Response& res) {
        res.set_content(presenter.stop_recording(), "application/json");
    });

    server.Get("/status", [this](const httplib::Request&, httplib::Response& res) {
        res.set_content(presenter.get_status(), "application/json");
    });

    server.Post("/set_quality", [this](const httplib::Request& req, httplib::Response& res) {
        auto json = nlohmann::json::parse(req.body);
        int width = json["width"];
        int height = json["height"];
        int fps = json["fps"];
        int bitrate = json["bitrate"];
        res.set_content(presenter.set_quality(width, height, fps, bitrate), "application/json");
    });

    server.Post("/set_storage_limit", [this](const httplib::Request& req, httplib::Response& res) {
        auto json = nlohmann::json::parse(req.body);
        size_t limit = json["limit"];
        res.set_content(presenter.set_storage_limit(limit), "application/json");
    });
}

void DashCamView::run(const std::string& host, int port) {
    server.listen(host.c_str(), port);
}