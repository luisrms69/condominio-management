# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Code Generator Module - Day 3 Portal Web
========================================

Generador de código automático en múltiples lenguajes para APIs documentadas.
"""

import json
from typing import Any, Optional

import frappe
from frappe import _


@frappe.whitelist()
def generate_api_code(api_name: str, language: str = "python", include_auth: bool = True) -> dict[str, Any]:
	"""
	Genera código de ejemplo para una API en el lenguaje especificado.

	Args:
		api_name: Nombre/ID de la API
		language: Lenguaje de programación (python, javascript, curl, php, etc.)
		include_auth: Incluir autenticación en el código

	Returns:
		Dict con código generado
	"""
	try:
		# Obtener detalles de la API
		api_doc = frappe.get_doc("API Documentation", api_name)

		# Obtener parámetros
		parameters = frappe.get_all(
			"API Parameter",
			filters={"parent": api_name, "is_required": 1},
			fields=["parameter_name", "data_type", "default_value", "parameter_description"],
			order_by="idx",
		)

		# Generar código según el lenguaje
		code_generators = {
			"python": _generate_python_code,
			"javascript": _generate_javascript_code,
			"curl": _generate_curl_code,
			"php": _generate_php_code,
			"java": _generate_java_code,
			"go": _generate_go_code,
		}

		if language not in code_generators:
			return {
				"success": False,
				"error": f"Lenguaje {language} no soportado",
				"supported_languages": list(code_generators.keys()),
			}

		generator = code_generators[language]
		code = generator(api_doc, parameters, include_auth)

		return {
			"success": True,
			"code": code,
			"language": language,
			"api_name": api_doc.api_name,
			"description": f"Código de ejemplo en {language.title()} para {api_doc.api_name}",
		}

	except Exception as e:
		frappe.log_error(f"Error generating code for {api_name}: {e!s}", "Code Generator")
		return {"success": False, "error": str(e)}


def _generate_python_code(api_doc, parameters: list[dict], include_auth: bool) -> str:
	"""Genera código Python usando requests"""

	# Construir URL
	base_url = frappe.utils.get_url()
	api_path = api_doc.api_path
	if not api_path.startswith("/api/method/"):
		api_path = f"/api/method{api_path}"
	full_url = f"{base_url}{api_path}"

	# Generar parámetros de ejemplo
	example_params = {}
	for param in parameters:
		example_params[param["parameter_name"]] = _get_example_value(
			param["data_type"], param.get("default_value")
		)

	# Generar código
	code = f"""import requests
import json

# API: {api_doc.api_name}
# {api_doc.description or "Sin descripción"}

url = "{full_url}"
"""

	if include_auth and api_doc.authentication_required:
		code += """
# Autenticación requerida
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY_HERE",
    "X-Frappe-CSRF-Token": "YOUR_CSRF_TOKEN"
}
"""
	else:
		code += """
headers = {
    "Content-Type": "application/json"
}
"""

	if example_params:
		code += f"""
# Parámetros del request
data = {json.dumps(example_params, indent=4)}
"""
	else:
		code += """
# Sin parámetros requeridos
data = {}
"""

	method = api_doc.http_method.lower()
	if method == "get":
		code += """
# Ejecutar request GET
response = requests.get(url, params=data, headers=headers)
"""
	else:
		code += f"""
# Ejecutar request {method.upper()}
response = requests.{method}(url, json=data, headers=headers)
"""

	code += """
# Procesar respuesta
if response.status_code == 200:
    result = response.json()
    print("Success:", result)
else:
    print(f"Error {response.status_code}: {response.text}")
"""

	return code


def _generate_javascript_code(api_doc, parameters: list[dict], include_auth: bool) -> str:
	"""Genera código JavaScript usando fetch"""

	base_url = frappe.utils.get_url()
	api_path = api_doc.api_path
	if not api_path.startswith("/api/method/"):
		api_path = f"/api/method{api_path}"
	full_url = f"{base_url}{api_path}"

	example_params = {}
	for param in parameters:
		example_params[param["parameter_name"]] = _get_example_value(
			param["data_type"], param.get("default_value")
		)

	code = f"""// API: {api_doc.api_name}
// {api_doc.description or "Sin descripción"}

const url = "{full_url}";
"""

	if include_auth and api_doc.authentication_required:
		code += """
// Configuración con autenticación
const headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY_HERE",
    "X-Frappe-CSRF-Token": getCsrfToken() // Función para obtener CSRF token
};
"""
	else:
		code += """
const headers = {
    "Content-Type": "application/json"
};
"""

	if example_params:
		code += f"""
// Parámetros del request
const data = {json.dumps(example_params, indent=4)};
"""
	else:
		code += """
// Sin parámetros requeridos
const data = {};
"""

	method = api_doc.http_method.upper()
	if method == "GET":
		code += """
// Ejecutar request GET
const queryString = new URLSearchParams(data).toString();
const fullUrl = queryString ? `${url}?${queryString}` : url;

fetch(fullUrl, {
    method: "GET",
    headers: headers
})
"""
	else:
		code += f"""
// Ejecutar request {method}
fetch(url, {{
    method: "{method}",
    headers: headers,
    body: JSON.stringify(data)
}})
"""

	code += """.then(response => {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
})
.then(data => {
    console.log("Success:", data);
})
.catch(error => {
    console.error("Error:", error);
});
"""

	return code


def _generate_curl_code(api_doc, parameters: list[dict], include_auth: bool) -> str:
	"""Genera comando cURL"""

	base_url = frappe.utils.get_url()
	api_path = api_doc.api_path
	if not api_path.startswith("/api/method/"):
		api_path = f"/api/method{api_path}"
	full_url = f"{base_url}{api_path}"

	example_params = {}
	for param in parameters:
		example_params[param["parameter_name"]] = _get_example_value(
			param["data_type"], param.get("default_value")
		)

	method = api_doc.http_method.upper()

	code = f'''# API: {api_doc.api_name}
# {api_doc.description or "Sin descripción"}

curl -X {method} "{full_url}" \\
  -H "Content-Type: application/json"'''

	if include_auth and api_doc.authentication_required:
		code += ''' \\
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \\
  -H "X-Frappe-CSRF-Token: YOUR_CSRF_TOKEN"'''

	if example_params and method != "GET":
		json_data = json.dumps(example_params, indent=2)
		code += f""" \\
  -d '{json_data}' """
	elif example_params and method == "GET":
		# Para GET, usar query parameters
		params = "&".join([f"{k}={v}" for k, v in example_params.items()])
		code = code.replace(f'"{full_url}"', f'"{full_url}?{params}"')

	return code


def _generate_php_code(api_doc, parameters: list[dict], include_auth: bool) -> str:
	"""Genera código PHP usando cURL"""

	base_url = frappe.utils.get_url()
	api_path = api_doc.api_path
	if not api_path.startswith("/api/method/"):
		api_path = f"/api/method{api_path}"
	full_url = f"{base_url}{api_path}"

	example_params = {}
	for param in parameters:
		example_params[param["parameter_name"]] = _get_example_value(
			param["data_type"], param.get("default_value")
		)

	code = f"""<?php
// API: {api_doc.api_name}
// {api_doc.description or "Sin descripción"}

$url = "{full_url}";
"""

	if example_params:
		php_params = json.dumps(example_params, indent=4)
		code += f"""$data = json_decode('{php_params}', true);
"""
	else:
		code += """$data = array();
"""

	code += """
// Inicializar cURL
$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
"""

	if include_auth and api_doc.authentication_required:
		code += """curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    "Content-Type: application/json",
    "Authorization: Bearer YOUR_API_KEY_HERE",
    "X-Frappe-CSRF-Token: YOUR_CSRF_TOKEN"
));
"""
	else:
		code += """curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    "Content-Type: application/json"
));
"""

	method = api_doc.http_method.upper()
	if method != "GET":
		code += f"""
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "{method}");
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
"""
	else:
		code += """
if (!empty($data)) {
    $url .= '?' . http_build_query($data);
    curl_setopt($ch, CURLOPT_URL, $url);
}
"""

	code += """
// Ejecutar request
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if ($response === false) {
    echo "cURL Error: " . curl_error($ch);
} else {
    echo "HTTP Code: " . $httpCode . "\\n";
    echo "Response: " . $response . "\\n";

    if ($httpCode == 200) {
        $data = json_decode($response, true);
        print_r($data);
    }
}

curl_close($ch);
?>
"""

	return code


def _generate_java_code(api_doc, parameters: list[dict], include_auth: bool) -> str:
	"""Genera código Java usando HttpURLConnection"""

	base_url = frappe.utils.get_url()
	api_path = api_doc.api_path
	if not api_path.startswith("/api/method/"):
		api_path = f"/api/method{api_path}"
	full_url = f"{base_url}{api_path}"

	example_params = {}
	for param in parameters:
		example_params[param["parameter_name"]] = _get_example_value(
			param["data_type"], param.get("default_value")
		)

	code = f"""import java.io.*;
import java.net.*;
import java.util.*;

// API: {api_doc.api_name}
// {api_doc.description or "Sin descripción"}

public class APIClient {{
    public static void main(String[] args) {{
        try {{
            String url = "{full_url}";
"""

	if example_params:
		json_data = json.dumps(example_params)
		code += f"""            String jsonData = "{json_data}";
"""
	else:
		code += """            String jsonData = "{}";
"""

	code += """
            URL apiUrl = new URL(url);
            HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();

"""

	method = api_doc.http_method.upper()
	code += f"""            connection.setRequestMethod("{method}");
            connection.setRequestProperty("Content-Type", "application/json");
"""

	if include_auth and api_doc.authentication_required:
		code += """            connection.setRequestProperty("Authorization", "Bearer YOUR_API_KEY_HERE");
            connection.setRequestProperty("X-Frappe-CSRF-Token", "YOUR_CSRF_TOKEN");
"""

	if method != "GET":
		code += """
            connection.setDoOutput(true);

            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = jsonData.getBytes("utf-8");
                os.write(input, 0, input.length);
            }
"""

	code += """
            int responseCode = connection.getResponseCode();
            BufferedReader reader;

            if (responseCode >= 200 && responseCode < 300) {
                reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            } else {
                reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
            }

            String line;
            StringBuilder response = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();

            System.out.println("Response Code: " + responseCode);
            System.out.println("Response: " + response.toString());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
"""

	return code


def _generate_go_code(api_doc, parameters: list[dict], include_auth: bool) -> str:
	"""Genera código Go usando net/http"""

	base_url = frappe.utils.get_url()
	api_path = api_doc.api_path
	if not api_path.startswith("/api/method/"):
		api_path = f"/api/method{api_path}"
	full_url = f"{base_url}{api_path}"

	example_params = {}
	for param in parameters:
		example_params[param["parameter_name"]] = _get_example_value(
			param["data_type"], param.get("default_value")
		)

	code = f"""package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
)

// API: {api_doc.api_name}
// {api_doc.description or "Sin descripción"}

func main() {{
    url := "{full_url}"
"""

	if example_params:
		go_params = json.dumps(example_params, indent=4)
		code += f"""
    data := map[string]interface{{}}{{}}
    jsonStr := `{go_params}`
    json.Unmarshal([]byte(jsonStr), &data)

    jsonData, _ := json.Marshal(data)
"""
	else:
		code += """
    jsonData := []byte("{}")
"""

	method = api_doc.http_method.upper()
	if method == "GET":
		code += """
    req, err := http.NewRequest("GET", url, nil)
"""
	else:
		code += f"""
    req, err := http.NewRequest("{method}", url, bytes.NewBuffer(jsonData))
"""

	code += """    if err != nil {
        panic(err)
    }

    req.Header.Set("Content-Type", "application/json")
"""

	if include_auth and api_doc.authentication_required:
		code += """    req.Header.Set("Authorization", "Bearer YOUR_API_KEY_HERE")
    req.Header.Set("X-Frappe-CSRF-Token", "YOUR_CSRF_TOKEN")
"""

	code += """
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Status Code: %d\\n", resp.StatusCode)
    fmt.Printf("Response: %s\\n", string(body))
}
"""

	return code


def _get_example_value(data_type: str, default_value: str | None = None):
	"""Genera valor de ejemplo para un tipo de dato"""
	if default_value:
		return default_value

	examples = {
		"string": "ejemplo_string",
		"integer": 123,
		"int": 123,
		"float": 12.34,
		"boolean": True,
		"bool": True,
		"object": {},
		"array": [],
		"list": [],
		"date": "2025-07-13",
		"datetime": "2025-07-13 18:00:00",
	}

	return examples.get(data_type.lower(), "valor_ejemplo")


@frappe.whitelist()
def get_supported_languages() -> list[str]:
	"""Obtiene lista de lenguajes soportados para generación de código"""
	return ["python", "javascript", "curl", "php", "java", "go"]
