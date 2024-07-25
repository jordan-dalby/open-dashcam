#pragma once
#include <string>
#include "presenter.h"
#include <httplib.h>

class DashCamView {
public:
    DashCamView(DashCamPresenter& presenter);
    void run(const std::string& host, int port);

private:
    void setup_routes();
    DashCamPresenter& presenter;
    httplib::Server server;
};