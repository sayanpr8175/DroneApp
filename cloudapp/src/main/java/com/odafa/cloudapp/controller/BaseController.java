package com.odafa.cloudapp.controller;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;


import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;



import com.odafa.cloudapp.configuration.ConfigReader;


import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;


@Slf4j
@Controller
@RequiredArgsConstructor
public class BaseController {

    private final ConfigReader configurations;

	


    @GetMapping("/")
    public String indexPage(Model model){

		model.addAttribute("publicIp", getFillerPublicIpAddress());
		// model.addAttribute("publicIp", getPublicIpAddress());
		model.addAttribute("defaultSpeed", configurations.getDefaultSpeed());
		model.addAttribute("defaultAltitude", configurations.getDefaultAltitude());
		model.addAttribute("videoEndpoint", configurations.getVideoWsEndpoint());

        log.debug("Index page opened");
        return "index";
    }
    
    @GetMapping("/v/{droneId}")
	public String getVideoFeed(Model model, @PathVariable("droneId") String droneId) {
		
		// model.addAttribute("publicIp", getPublicIpAddress());
		model.addAttribute("publicIp", getFillerPublicIpAddress());
		
		model.addAttribute("droneId", droneId);
		model.addAttribute("videoEndpoint", configurations.getVideoWsEndpoint());
        
        //log.debug("dronevideo page opened");

        return "video";
    }


    private String getPublicIpAddress() {
		String ip = "";
		try {
			final URL whatismyip = new URL("http://checkip.amazonaws.com");

			try(final BufferedReader in = new BufferedReader(new InputStreamReader(whatismyip.openStream()))){
				ip = in.readLine();
			}

		} catch (Exception e) {
			log.error(e.getMessage());
		}
		return ip;
	}



	// For only my allianceBroadBand : Start

	private String getFillerPublicIpAddress() {
		String ip = "192.168.0.103";
		try {
			final URL whatismyip = new URL("http://checkip.amazonaws.com");

			try(final BufferedReader in = new BufferedReader(new InputStreamReader(whatismyip.openStream()))){
				//ip = in.readLine();
			}

		} catch (Exception e) {
			log.error(e.getMessage());
		}
		return ip;
	}

	// For only my allianceBroadBand : End


}
