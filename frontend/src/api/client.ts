import axios, { type AxiosInstance } from "axios";

let isRefreshing = false;
let pendingQueue: Array<(success: boolean) => void> = [];

function processQueue(success: boolean) {
	pendingQueue.forEach((cb) => cb(success));
	pendingQueue = [];
}

const api: AxiosInstance = axios.create({ baseURL: "/" });

api.interceptors.response.use(
	(response) => response,
	async (error) => {
		const original = error.config;
		if (error.response?.status !== 401 || original._retry) {
			return Promise.reject(error);
		}
		original._retry = true;

		if (isRefreshing) {
			return new Promise((resolve, reject) => {
				pendingQueue.push((success) => {
					if (success) resolve(api(original));
					else reject(error);
				});
			});
		}

		isRefreshing = true;
		try {
			await axios.post("/api/auth/refresh");
			processQueue(true);
			return api(original);
		} catch (refreshError) {
			processQueue(false);
			window.dispatchEvent(new Event("auth:expired"));
			return Promise.reject(refreshError);
		} finally {
			isRefreshing = false;
		}
	},
);

export default api;
