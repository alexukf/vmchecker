package ro.pub.cs.vmchecker.client.model;

public class Assignment {
	public String id;
	public String title;
	public String storageType;
	public String storageHost;
	public String storageBasepath;
	public String deadline;
	public String statementLink;

	public Assignment(String id, String title, String storageType, String storageHost, String storageBasepath, String deadline, String statementLink) {
		this.id = id;
		this.title = title;
		this.storageType = storageType;
		this.storageHost = storageHost;
		this.storageBasepath = storageBasepath;
		this.storageType = storageType;
		this.deadline = deadline;
		this.statementLink = statementLink;
	}

}
